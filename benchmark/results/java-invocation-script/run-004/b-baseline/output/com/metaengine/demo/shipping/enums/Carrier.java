package com.metaengine.demo.shipping.enums;

/** Carrier enum in the shipping domain. */
public enum Carrier {
    Ups(0),
    Fedex(1),
    Dhl(2),
    Usps(3);

    private final int value;

    Carrier(int value) { this.value = value; }

    public int getValue() { return value; }
}
