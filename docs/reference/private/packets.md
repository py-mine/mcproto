# Internal components for packets

These are the utility components related to / used in the packets module.

!!! bug "Missing internal components of individual packets"

    The internal components which are specific to the individual packet classes (rather than being shared across the
    entire packets module) are not documented here. Documentation for these may be added in the future, but there is
    no timeframe for this, if you're interested in these, we recommend that you just check the source code instead.

::: mcproto.packets.packet_map
    options:
        members: [WalkableModuleData, _walk_submodules, _walk_module_packets]

::: mcproto.packets.interactions
    options:
        filters:
            - "^_[^_]"
