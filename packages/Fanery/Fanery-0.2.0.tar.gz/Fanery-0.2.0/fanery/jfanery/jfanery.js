/*
 * Fanery javascript client
 *
 * Project page.
 * 	https://pypi.python.org/pypi/Fanery
 * 	https://bitbucket.org/mcaramma/fanery
 *
 * Licensed under ISC license.
 * 	http://opensource.org/licenses/isc-license
*/

if (!this.Fanery && jQuery && nacl_factory && scrypt_module_factory && Base64 && JSON) {
  (function (global) {
    var self = global.Fanery = {};

    // private definition

    var _nacl = nacl_factory.instantiate(),
        _scrypt = scrypt_module_factory(),
        _atob = Base64.atob,
        _btoa = Base64.btoa,
        _q = jQuery,
        _auth = {},
        _geoip = null,
        _baseurl = location.origin || location.protocol + '//' + location.host,
        _state = {'domain': window.location.hostname,
                  'identity': null,
                  'logged': false};

    var utf8encode = _nacl.encode_utf8,
        utf8decode = _nacl.decode_utf8;

    function b64decode (b64enc) {
        return new Uint8Array(_atob(b64enc).split("").map(function (c) {
            return c.charCodeAt(0);
        }));
    };

    function b64encode (term) {
        if (term instanceof Uint8Array) {
            return _btoa(String.fromCharCode.apply(null, term));
        } else {
            return Base64.encode(term);
        }
    };

    function _xor (a1, a2) {
        var a1l = a1.length,
            a2l = a2.length,
            xored = new Uint8Array(a1l);
        for (var i = 0; i < a1l; i++) {
            xored[i] = a1[i] ^ a2[i > a2l ? i % a2l : i];
        }
        return xored;
    };

    function _timestamp () {
        return Math.round((new Date()).getTime() / 1000);
    };

    function _error (e) {
        var name = e.exc || e.name || 'System Error',
            messages = e.err || [e.message || 'An error occurred. Please contact the system administrator.'];
        (console ? console.error : alert)(name + ": " + (messages.join ? messages.join('\n') : messages));
    };

    function _unset_state () {
        _state.identity = null;
        _state.logged = false;
        _auth = {};
    }
    
    // preserve state during page transition
    
    function _preserve_state () {
        for (var k in _auth) {
            if (_auth.hasOwnProperty(k) && k.substr(k.length - 4) === '_key') {
                _auth[k] = b64encode(_auth[k]);
            }
        }
        window.name = 'jfnry:' + b64encode(JSON.stringify([_state,_auth,window.name]));
    }
    
    // restore state after page transition

    if (window.name.substr(0,6) === 'jfnry:') {
        try {
            var _temp = JSON.parse(utf8decode(b64decode(window.name.substr(6))));
            _q.extend(_state, _temp[0]);
            _q.extend(_auth, _temp[1]);
            for (var k in _auth) {
                if (_auth.hasOwnProperty(k) && k.substr(k.length - 4) === '_key') {
                    _auth[k] = b64decode(_auth[k]);
                }
            }
            window.name = _temp[2];
            console.debug(_state);
            console.debug(_auth);
        } catch(e) {}
    }

    // public definition

    self.urlpaths = {
        prelogin: _baseurl + '/prelogin.json',
        login: _baseurl + '/login.json',
        logout: _baseurl + '/logout.json',
        gen_pad: _baseurl + '/gen_pad.json'
    };

    self.password = {
	    hash_func: function (text, salt) {
			return _scrypt.crypto_scrypt(utf8encode(text), salt, 16384, 8, 1, 64);
		}
    };

    self.exc = {
        Error: _error,
        InvalidCredential: _error,
        Unauthorized: _error
    };

    self.handle_exc = function (e) {
        (self.exc[e.exc] || self.exc.Error)(e);
    };

    self.get_state = function () {
        return _q.extend({}, _state);
    };

    self.login = function (login, password, extra) {
        // prepare prelogin params
        var params = _q.extend({}, {'identity': login}, extra);
        var transition = params.transition || false;
        var force = params.force || false;
        delete params.transition;
        delete params.force;

        // chained prelogin+login & return login promise
        return _q.Deferred(function (defer) {
            self.call(self.urlpaths.prelogin, {'_json_': params}) // prelogin
                .then(function (ret) {
                    try {
                        // nacl decrypt based on password hash (scrypt by default)
                        var enc = b64decode(ret.enc),
                            nonce = enc.subarray(0,24),
                            enc = enc.subarray(24, enc.length),
                            pkey = b64decode(ret.pkey),
                            salt = b64decode(ret.salt),
                            hash = self.password.hash_func(password, salt),
                            skey = _nacl.crypto_hash_sha256(hash),
                            msg = _nacl.crypto_box_open(enc, nonce, pkey, skey),
                            sid = b64encode(msg.subarray(64, 80)),
                            cseed = msg.subarray(0, 32),
                            vkey = msg.subarray(32, 64),
                            pad = msg.subarray(80, msg.length);

                        // prepare login params
                        var sk = _nacl.crypto_sign_keypair_from_seed(cseed).signSk,
                            sign = _nacl.crypto_sign(hash, sk).subarray(0, 64),
                            argd = {'sign': b64encode(_xor(sign, pad)),
                                    'identity': login,
                                    'sid': sid,
                                    'force': force};

                        // login & trigger defer
                        self.call(self.urlpaths.login, argd)
                            .then(function done (ret) {
                                try {
                                    // nacl decrypt based on prelogin data 
                                    var enc = _nacl.crypto_sign_open(b64decode(ret.sign), vkey),
                                        nonce = enc.subarray(0, 24),
                                        enc = enc.subarray(24, enc.length),
                                        msg = _nacl.crypto_box_open(enc, nonce, pkey, skey),
                                        ts = parseInt(utf8decode(msg.subarray(64, msg.length)));

                                    // update session state
                                    _state.identity = login;
                                    _state.logged = true;

                                    // set authentication keys (used during safe_call)
                                    _auth.identity = login;
                                    _auth.sid = sid;
                                    _auth.sign_key = sk;
                                    _auth.verify_key = vkey;
                                    _auth.client_key = msg.subarray(0, 32);
                                    _auth.server_key = msg.subarray(32, 64);
                                    _auth.tdiff = ts - _timestamp();

                                    // if transition to other page expected
                                    if (transition) {
                                        _preserve_state();
                                    }

                                    // done
                                    defer.resolve(true);
                                } catch(e) {
                                    _unset_state();
                                    defer.reject(e);
                                    self.handle_exc(e);
                                }
                            }, defer.reject);

                    // invalid credentials
                    } catch(e) {
                        var err = {'exc': 'InvalidCredential', 'err': 'bad username or password', 'low': true};
                        _unset_state();
                        defer.reject(err);
                        self.handle_exc(err);
                    }
                }, defer.reject);
            }).promise();
    };

    self.logout = function () {
        return self.safe_call('logout').then(function(ret) {
            _unset_state();
            return ret;
        }).promise();
    };

    self.safe_call = function (urlpath, argd) {
        // must have valid session
        if (!_state.logged) {
            var e = {'exc': 'Unauthorized', 'err': 'must login', 'low': true};
            return _q.Deferred(function (defer) {
                self.handle_exc(e);
                defer.reject(e);
            }).promise();
        }

        // prepare gen_pad call params
        var params = JSON.stringify(argd || {}),
            size = params.length + 40,
            pad = _nacl.random_bytes(size + 340),
            nonce = _nacl.crypto_box_random_nonce(),
            msg = utf8encode(JSON.stringify({'call': urlpath,
                                             'pad': b64encode(pad),
                                             'tstamp': _timestamp() + _auth.tdiff})),
            enc = _nacl.crypto_box(msg, nonce, _auth.server_key, _auth.client_key);

        // pynacl.public.Box expect nonce+enc but crypto_box do not prepend nonce by default
        var full_enc = new Uint8Array(nonce.length + enc.length);
        full_enc.set(nonce, 0);
        full_enc.set(enc, nonce.length);

        // compute sign
        var sign = b64encode(_nacl.crypto_sign(full_enc, _auth.sign_key));

        // chained gen_pad+urlpath & return urlpath call promise
        return _q.Deferred(function (defer) {
            self.call(self.urlpaths.gen_pad, {'_json_': {'sid': _auth.sid, 'sign': sign}}) // gen_pad
                .then(function (ret) {
                        try {
                            // nacl decrypt based on gen_pad
                            var xored = _nacl.crypto_sign_open(b64decode(ret.sign), _auth.verify_key),
                                enc = _xor(xored, pad),
                                nonce = enc.subarray(0, 24),
                                enc = enc.subarray(24, enc.length),
                                msg = _nacl.crypto_box_open(enc, nonce, _auth.server_key, _auth.client_key),
                                cpad = JSON.parse(utf8decode(msg));
                            
                            // prepare `urlpath` params
                            var nonce = _nacl.crypto_box_random_nonce(),
                                cpad_skey = b64decode(cpad.skey),
                                cpad_ckey = b64decode(cpad.ckey),
                                enc = _nacl.crypto_box(utf8encode(params), nonce, cpad_skey, cpad_ckey);

                            // again, pynacl.public.Box expect nonce+enc but crypto_box do not prepend nonce by default
                            var full_enc = new Uint8Array(nonce.length + enc.length);
                            full_enc.set(nonce, 0);
                            full_enc.set(enc, nonce.length);

                            // compute sign
                            var xored = _xor(full_enc, b64decode(cpad.pad)),
                                sk = _nacl.crypto_sign_keypair_from_seed(b64decode(cpad.cseed)),
                                sign = b64encode(_nacl.crypto_sign(xored, sk.signSk));

                            self.call(_baseurl + '/' + urlpath, {'sign': sign, 'sid': _auth.sid, 'pid': cpad.pid})
                                .then(function (ret) {
                                        try {
                                            // nacl decrypt based on cpad data 
                                            var enc = _nacl.crypto_sign_open(b64decode(ret.sign), b64decode(cpad.vkey)),
                                                nonce = enc.subarray(0, 24),
                                                enc = enc.subarray(24, enc.length),
                                                msg = _nacl.crypto_box_open(enc, nonce, cpad_skey, cpad_ckey),
                                                json = JSON.parse(utf8decode(msg));

                                        } catch(e) {
                                            defer.reject(e);
                                            self.handle_exc(e);
                                            return;
                                        }

                                        // done
                                        if (json && json.exc) {
                                            defer.reject(json);
                                            self.handle_exc(json);
                                        } else {
                                            defer.resolve(json);
                                        }
                                    }, function (e) {
                                        var err = e.responseJSON || e;
                                        defer.reject(err);
                                        self.handle_exc(err);
                                    });
                        } catch(e) {
                            defer.reject(e);
                            self.handle_exc(e);
                        }
                }, function (e) {
                    var err = e.responseJSON || e;
                    if (/Session/.test(err.exc))
                        _unset_state();
                    defer.reject(err);
                    self.handle_exc(err);
                });
	     }).promise();
    };

    self.call = function (service, params, settings) {
        // make sure to call `service` with proper settings if json response is expected
        if (((settings || {}).dataType || 'json') == 'json' && service.indexOf('.json', service.length - 5) < 0) {
            service = service + '.json';
        }
        if (params && params._json_) {
            params._json_ = JSON.stringify(params._json_);
        }

        // return urlpath call promise
        return _q.Deferred(function (defer) {
            return _q.ajax(service, _q.extend({
                                'type': 'POST',
                                'async': true,
                                'cache': false,
                                'dataType': 'json',
                                'data': params
                            }, settings))
                    .then(defer.resolve, function (e) {
                        var err = e.responseJSON || e;
                        defer.reject(err);
                        self.handle_exc(err);
                    });
        }).promise();
    };

    // third party geolocation service

    self.geoip = function () {
        if (!_geoip) {
            _q.getJSON("http://www.telize.com/geoip?callback=?",
                function(json) {
                    _geoip = json;
                });
        }
        return _geoip;
    }

  })(this);
};
