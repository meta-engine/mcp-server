package com.metaengine.demo.inventory.enums;

/** StockState enum for the inventory domain. */
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
}
