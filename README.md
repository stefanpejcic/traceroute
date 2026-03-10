# traceroute
Example plugin for OpenPanel

This is an example plugin for OpenPanel.

[![2025-07-21-14-34.png](https://i.postimg.cc/X7cTZdzx/2025-07-21-14-34.png)](https://postimg.cc/w7MWZyHs)

Installation:
```bash
cd /etc/openpanel/modules/ && git clone https://github.com/stefanpejcic/traceroute && \
  docker restart openpanel
```

Update:
```bash
rm -rf /etc/openpanel/modules/traceroute && \
  cd /etc/openpanel/modules/ && git clone https://github.com/stefanpejcic/traceroute && \
  docker restart openpanel
```

---

Documentation: https://openpanel.com/docs/articles/dev-experience/custom-plugins#example
