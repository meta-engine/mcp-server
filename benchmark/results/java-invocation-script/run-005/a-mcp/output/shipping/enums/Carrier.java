package com.metaengine.demo.shipping.enums;

// Carrier enum.

public enum Carrier {
    UPS(0),
    FEDEX(1),
    DHL(2),
    USPS(3);

    private final int value;

    Carrier(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static Carrier fromValue(int value) {
        for (Carrier item : Carrier.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}
