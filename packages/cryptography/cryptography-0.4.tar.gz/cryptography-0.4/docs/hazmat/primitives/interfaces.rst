.. hazmat::

Interfaces
==========


``cryptography`` uses `Abstract Base Classes`_ as interfaces to describe the
properties and methods of most primitive constructs. Backends may also use
this information to influence their operation. Interfaces should also be used
to document argument and return types.

.. _`Abstract Base Classes`: http://docs.python.org/3.2/library/abc.html


Symmetric ciphers
~~~~~~~~~~~~~~~~~

.. currentmodule:: cryptography.hazmat.primitives.interfaces


.. class:: CipherAlgorithm

    A named symmetric encryption algorithm.

    .. attribute:: name

        :type: str

        The standard name for the mode, for example, "AES", "Camellia", or
        "Blowfish".

    .. attribute:: key_size

        :type: int

        The number of bits in the key being used.


.. class:: BlockCipherAlgorithm

    A block cipher algorithm.

    .. attribute:: block_size

        :type: int

        The number of bits in a block.


Cipher modes
------------

Interfaces used by the symmetric cipher modes described in
:ref:`Symmetric Encryption Modes <symmetric-encryption-modes>`.

.. class:: Mode

    A named cipher mode.

    .. attribute:: name

        :type: str

        This should be the standard shorthand name for the mode, for example
        Cipher-Block Chaining mode is "CBC".

        The name may be used by a backend to influence the operation of a
        cipher in conjunction with the algorithm's name.

    .. method:: validate_for_algorithm(algorithm)

        :param CipherAlgorithm algorithm:

        Checks that the combination of this mode with the provided algorithm
        meets any necessary invariants. This should raise an exception if they
        are not met.

        For example, the :class:`~cryptography.hazmat.primitives.modes.CBC`
        mode uses this method to check that the provided initialization
        vector's length matches the block size of the algorithm.


.. class:: ModeWithInitializationVector

    A cipher mode with an initialization vector.

    .. attribute:: initialization_vector

        :type: bytes

        Exact requirements of the initialization are described by the
        documentation of individual modes.


.. class:: ModeWithNonce

    A cipher mode with a nonce.

    .. attribute:: nonce

        :type: bytes

        Exact requirements of the nonce are described by the documentation of
        individual modes.

Asymmetric interfaces
~~~~~~~~~~~~~~~~~~~~~

.. class:: RSAPrivateKey

    .. versionadded:: 0.2

    An `RSA`_ private key.

    .. method:: signer(padding, algorithm, backend)

        .. versionadded:: 0.3

        Sign data which can be verified later by others using the public key.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricSignatureContext`

    .. method:: decrypt(ciphertext, padding, backend)

        .. versionadded:: 0.4

        Decrypt data that was encrypted via the public key.

        :param bytes ciphertext: The ciphertext to decrypt.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :return bytes: Decrypted data.

    .. method:: public_key()

        :return: :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`

        An RSA public key object corresponding to the values of the private key.

    .. attribute:: modulus

        :type: int

        The public modulus.

    .. attribute:: public_exponent

        :type: int

        The public exponent.

    .. attribute:: private_exponent

        :type: int

        The private exponent.

    .. attribute:: key_size

        :type: int

        The bit length of the modulus.

    .. attribute:: p

        :type: int

        ``p``, one of the two primes composing the :attr:`modulus`.

    .. attribute:: q

        :type: int

        ``q``, one of the two primes composing the :attr:`modulus`.

    .. attribute:: d

        :type: int

        The private exponent. Alias for :attr:`private_exponent`.

    .. attribute:: dmp1

        :type: int

        A `Chinese remainder theorem`_ coefficient used to speed up RSA
        operations. Calculated as: d mod (p-1)

    .. attribute:: dmq1

        :type: int

        A `Chinese remainder theorem`_ coefficient used to speed up RSA
        operations. Calculated as: d mod (q-1)

    .. attribute:: iqmp

        :type: int

        A `Chinese remainder theorem`_ coefficient used to speed up RSA
        operations. Calculated as: q\ :sup:`-1` mod p

    .. attribute:: n

        :type: int

        The public modulus. Alias for :attr:`modulus`.

    .. attribute:: e

        :type: int

        The public exponent. Alias for :attr:`public_exponent`.


.. class:: RSAPublicKey

    .. versionadded:: 0.2

    An `RSA`_ public key.

    .. method:: verifier(signature, padding, algorithm, backend)

        .. versionadded:: 0.3

        Verify data was signed by the private key associated with this public
        key.

        :param bytes signature: The signature to verify.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricVerificationContext`

    .. method:: encrypt(plaintext, padding, backend)

        .. versionadded:: 0.4

        Encrypt data with the public key.

        :param bytes plaintext: The plaintext to encrypt.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :return bytes: Encrypted data.

    .. attribute:: modulus

        :type: int

        The public modulus.

    .. attribute:: key_size

        :type: int

        The bit length of the modulus.

    .. attribute:: public_exponent

        :type: int

        The public exponent.

    .. attribute:: n

        :type: int

        The public modulus. Alias for :attr:`modulus`.

    .. attribute:: e

        :type: int

        The public exponent. Alias for :attr:`public_exponent`.


.. class:: DSAParameters

    .. versionadded:: 0.3

    `DSA`_ parameters.

    .. attribute:: modulus

        :type: int

        The prime modulus that is used in generating the DSA key pair and used
        in the DSA signing and verification processes.

    .. attribute:: subgroup_order

        :type: int

        The subgroup order that is used in generating the DSA key pair
        by the generator and used in the DSA signing and verification
        processes.

    .. attribute:: generator

        :type: int

        The generator that is used in generating the DSA key pair and used
        in the DSA signing and verification processes.

    .. attribute:: p

        :type: int

        The prime modulus that is used in generating the DSA key pair and used
        in the DSA signing and verification processes. Alias for :attr:`modulus`.

    .. attribute:: q

        :type: int

        The subgroup order that is used in generating the DSA key pair
        by the generator and used in the DSA signing and verification
        processes. Alias for :attr:`subgroup_order`.

    .. attribute:: g

        :type: int

        The generator that is used in generating the DSA key pair and used
        in the DSA signing and verification processes. Alias for :attr:`generator`.


.. class:: DSAPrivateKey

    .. versionadded:: 0.3

    A `DSA`_ private key.

    .. method:: public_key()

        :return: :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`

        An DSA public key object corresponding to the values of the private key.

    .. method:: parameters()

        :return: :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`

        The DSAParameters object associated with this private key.

    .. method:: signer(algorithm, backend)

        .. versionadded:: 0.4

        Sign data which can be verified later by others using the public key.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricSignatureContext`

    .. attribute:: key_size

        :type: int

        The bit length of the modulus.

    .. attribute:: x

        :type: int

        The private key.

    .. attribute:: y

        :type: int

        The public key.


.. class:: DSAPublicKey

    .. versionadded:: 0.3

    A `DSA`_ public key.

    .. attribute:: key_size

        :type: int

        The bit length of the modulus.

    .. attribute:: y

        :type: int

        The public key.

    .. method:: parameters()

        :return: :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`

        The DSAParameters object associated with this public key.

    .. method:: verifier(signature, algorithm, backend)

        .. versionadded:: 0.4

        Verify data was signed by the private key associated with this public
        key.

        :param bytes signature: The signature to verify. DER encoded as
            specified in :rfc:`6979`.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricVerificationContext`


.. class:: AsymmetricSignatureContext

    .. versionadded:: 0.2

    .. method:: update(data)

        :param bytes data: The data you want to sign.

    .. method:: finalize()

        :return bytes signature: The signature.


.. class:: AsymmetricVerificationContext

    .. versionadded:: 0.2

    .. method:: update(data)

        :param bytes data: The data you wish to verify using the signature.

    .. method:: verify()

        :raises cryptography.exceptions.InvalidSignature: If the signature does
            not validate.


.. class:: AsymmetricPadding

    .. versionadded:: 0.2

    .. attribute:: name

Hash algorithms
~~~~~~~~~~~~~~~

.. class:: HashAlgorithm

    .. attribute:: name

        :type: str

        The standard name for the hash algorithm, for example: ``"sha256"`` or
        ``"whirlpool"``.

    .. attribute:: digest_size

        :type: int

        The size of the resulting digest in bytes.

    .. attribute:: block_size

        :type: int

        The internal block size of the hash algorithm in bytes.


.. class:: HashContext

    .. attribute:: algorithm

        A :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm` that
        will be used by this context.

    .. method:: update(data)

        :param data bytes: The data you want to hash.

    .. method:: finalize()

        :return: The final digest as bytes.

    .. method:: copy()

        :return: A :class:`~cryptography.hazmat.primitives.interfaces.HashContext`
             that is a copy of the current context.


Key derivation functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: KeyDerivationFunction

    .. versionadded:: 0.2

    .. method:: derive(key_material)

        :param key_material bytes: The input key material. Depending on what
                                   key derivation function you are using this
                                   could be either random material, or a user
                                   supplied password.
        :return: The new key.
        :raises cryptography.exceptions.AlreadyFinalized: This is raised when
                                                          :meth:`derive` or
                                                          :meth:`verify` is
                                                          called more than
                                                          once.

        This generates and returns a new key from the supplied key material.

    .. method:: verify(key_material, expected_key)

        :param key_material bytes: The input key material. This is the same as
                                   ``key_material`` in :meth:`derive`.
        :param expected_key bytes: The expected result of deriving a new key,
                                   this is the same as the return value of
                                   :meth:`derive`.
        :raises cryptography.exceptions.InvalidKey: This is raised when the
                                                    derived key does not match
                                                    the expected key.
        :raises cryptography.exceptions.AlreadyFinalized: This is raised when
                                                          :meth:`derive` or
                                                          :meth:`verify` is
                                                          called more than
                                                          once.

        This checks whether deriving a new key from the supplied
        ``key_material`` generates the same key as the ``expected_key``, and
        raises an exception if they do not match. This can be used for
        something like checking whether a user's password attempt matches the
        stored derived key.


`CMAC`_
~~~~~~~

.. class:: CMACContext

    .. versionadded:: 0.4

    .. method:: update(data)

        :param data bytes: The data you want to authenticate.

    .. method:: finalize()

        :return: The message authentication code.

    .. method:: copy()

        :return: A :class:`~cryptography.hazmat.primitives.interfaces.CMACContext`
            that is a copy of the current context.


.. _`RSA`: https://en.wikipedia.org/wiki/RSA_(cryptosystem)
.. _`Chinese remainder theorem`: https://en.wikipedia.org/wiki/Chinese_remainder_theorem
.. _`DSA`: https://en.wikipedia.org/wiki/Digital_Signature_Algorithm
.. _`CMAC`: https://en.wikipedia.org/wiki/CMAC
