package com.metaengine.demo.shipping.enums;

/** Lifecycle states for a shipment. */
public enum ShipmentState {
    Pending(0),
    InTransit(1),
    Delivered(2),
    Lost(3);

    private final int value;

    ShipmentState(int value) { this.value = value; }

    public int getValue() { return value; }
}
