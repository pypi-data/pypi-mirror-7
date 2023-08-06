# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

import six

from cryptography import utils
from cryptography.exceptions import (
    InvalidSignature, UnsupportedAlgorithm, _Reasons
)
from cryptography.hazmat.primitives import hashes, interfaces
from cryptography.hazmat.primitives.asymmetric import ec


def _truncate_digest_for_ecdsa(ec_key_cdata, digest, backend):
    _lib = backend._lib
    _ffi = backend._ffi

    digest_len = len(digest)

    group = _lib.EC_KEY_get0_group(ec_key_cdata)

    bn_ctx = _lib.BN_CTX_new()
    assert bn_ctx != _ffi.NULL
    bn_ctx = _ffi.gc(bn_ctx, _lib.BN_CTX_free)

    order = _lib.BN_CTX_get(bn_ctx)
    assert order != _ffi.NULL

    res = _lib.EC_GROUP_get_order(group, order, bn_ctx)
    assert res == 1

    order_bits = _lib.BN_num_bits(order)

    if 8 * digest_len > order_bits:
        digest_len = (order_bits + 7) // 8
        digest = digest[:digest_len]

    if 8 * digest_len > order_bits:
        rshift = 8 - (order_bits & 0x7)
        assert rshift > 0 and rshift < 8

        mask = 0xFF >> rshift << rshift

        # Set the bottom rshift bits to 0
        digest = digest[:-1] + six.int2byte(six.indexbytes(digest, -1) & mask)

    return digest


@utils.register_interface(interfaces.AsymmetricSignatureContext)
class _ECDSASignatureContext(object):
    def __init__(self, backend, private_key, algorithm):
        self._backend = backend
        self._private_key = private_key
        self._digest = hashes.Hash(algorithm, backend)

    def update(self, data):
        self._digest.update(data)

    def finalize(self):
        ec_key = self._private_key._ec_key

        digest = self._digest.finalize()

        digest = _truncate_digest_for_ecdsa(ec_key, digest, self._backend)

        max_size = self._backend._lib.ECDSA_size(ec_key)
        assert max_size > 0

        sigbuf = self._backend._ffi.new("char[]", max_size)
        siglen_ptr = self._backend._ffi.new("unsigned int[]", 1)
        res = self._backend._lib.ECDSA_sign(
            0,
            digest,
            len(digest),
            sigbuf,
            siglen_ptr,
            ec_key
        )
        assert res == 1
        return self._backend._ffi.buffer(sigbuf)[:siglen_ptr[0]]


@utils.register_interface(interfaces.AsymmetricVerificationContext)
class _ECDSAVerificationContext(object):
    def __init__(self, backend, public_key, signature, algorithm):
        self._backend = backend
        self._public_key = public_key
        self._signature = signature
        self._digest = hashes.Hash(algorithm, backend)

    def update(self, data):
        self._digest.update(data)

    def verify(self):
        ec_key = self._public_key._ec_key

        digest = self._digest.finalize()

        digest = _truncate_digest_for_ecdsa(ec_key, digest, self._backend)

        res = self._backend._lib.ECDSA_verify(
            0,
            digest,
            len(digest),
            self._signature,
            len(self._signature),
            ec_key
        )
        if res != 1:
            self._backend._consume_errors()
            raise InvalidSignature
        return True


@utils.register_interface(interfaces.EllipticCurvePrivateKey)
class _EllipticCurvePrivateKey(object):
    def __init__(self, backend, ec_key_cdata, curve):
        self._backend = backend
        self._ec_key = ec_key_cdata
        self._curve = curve

    @property
    def curve(self):
        return self._curve

    def signer(self, signature_algorithm):
        if isinstance(signature_algorithm, ec.ECDSA):
            return _ECDSASignatureContext(
                self._backend, self, signature_algorithm.algorithm
            )
        else:
            raise UnsupportedAlgorithm(
                "Unsupported elliptic curve signature algorithm.",
                _Reasons.UNSUPPORTED_PUBLIC_KEY_ALGORITHM)

    def public_key(self):
        group = self._backend._lib.EC_KEY_get0_group(self._ec_key)
        assert group != self._backend._ffi.NULL

        curve_nid = self._backend._lib.EC_GROUP_get_curve_name(group)

        public_ec_key = self._backend._lib.EC_KEY_new_by_curve_name(curve_nid)
        assert public_ec_key != self._backend._ffi.NULL
        public_ec_key = self._backend._ffi.gc(
            public_ec_key, self._backend._lib.EC_KEY_free
        )

        point = self._backend._lib.EC_KEY_get0_public_key(self._ec_key)
        assert point != self._backend._ffi.NULL

        res = self._backend._lib.EC_KEY_set_public_key(public_ec_key, point)
        assert res == 1

        return _EllipticCurvePublicKey(
            self._backend, public_ec_key, self._curve
        )


@utils.register_interface(interfaces.EllipticCurvePublicKey)
class _EllipticCurvePublicKey(object):
    def __init__(self, backend, ec_key_cdata, curve):
        self._backend = backend
        self._ec_key = ec_key_cdata
        self._curve = curve

    @property
    def curve(self):
        return self._curve

    def verifier(self, signature, signature_algorithm):
        if isinstance(signature_algorithm, ec.ECDSA):
            return _ECDSAVerificationContext(
                self._backend, self, signature, signature_algorithm.algorithm
            )
        else:
            raise UnsupportedAlgorithm(
                "Unsupported elliptic curve signature algorithm.",
                _Reasons.UNSUPPORTED_PUBLIC_KEY_ALGORITHM)
