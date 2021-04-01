#!/usr/bin/env bash

service puppet stop
service pe-puppetserver reload
rm -rf /etc/puppetlabs/puppetserver/code/environments/*
rm -rf /etc/puppetlabs/code-staging/environments/*
rm -rf /opt/puppetlabs/server/data/code-manager/worker-caches/deploy-pool-*
