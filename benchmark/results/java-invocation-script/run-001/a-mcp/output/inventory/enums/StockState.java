package com.metaengine.demo.inventory.enums;

// StockState enum.

public enum StockState {
    IN_STOCK(0),
    RESERVED(1),
    DEPLETED(2);

    private final int value;

    StockState(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static StockState fromValue(int value) {
        for (StockState item : StockState.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}
