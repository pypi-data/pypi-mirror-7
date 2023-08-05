ec2yaml
========


Take a yaml file like this ::

    app:
      name: foo
      owner: adam venturella
      location: us-west-2
      key: <optional>
      secret: <optional>

    instances:
      app_server:
        key_name: aventurella
        image: ami-6ac2a85a
        size: m3.medium
        zone: us-west-2c

        ip_address: foo

        security_groups:
          - ssh
          - http
          - https
          - foo-salt
          - foo-ssh

        volumes:
          - foo-volume: /dev/sdh

    elastic_ips:
      - foo

    volumes:
        foo-volume:
            size: 1
            zone: us-west-2c

    security_groups:
      foo-ssh:
        ip_protocol: tcp
        from_port: 1022
        to_port: 1022
        cidr_ip: '0.0.0.0/0'

      foo-salt:
        ip_protocol: tcp
        from_port: 2000
        to_port: 65535
        cidr_ip: '0.0.0.0/0'


And materialize it into AWS EC2 accordingly.
