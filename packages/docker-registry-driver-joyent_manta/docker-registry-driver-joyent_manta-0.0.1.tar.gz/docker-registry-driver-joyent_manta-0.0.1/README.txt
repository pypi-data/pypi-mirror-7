Docker registry manta driver
=====

sudo pip install docker-registry-manta-driver

update config to using manta storage:
``
joyent_manta: &joyent_manta
    <<: *common
    storage: joyent_manta
    path: _env:REGISTRY_PATH:'/%s/stor/registry'
    url: _env:MANTA_URL:'https://us-east.manta.joyent.com/'
    insecure: _env:MANTA_TLS_INSECURE:False
    key_id: _env:MANTA_KEY_ID
    private_key: _env:MANTA_PRIVATE_KEY
    account: _env:MANTA_USER
``

or append env variables to docker-registry startup script
``
MANTA_USER=<Active manta username>
MANTA_KEY_ID=<SSH Key Fingerprint>
MANTA_URL='https://us-east.manta.joyent.com/'
REGISTRY_PATH='/%s/stor/registry'
``
