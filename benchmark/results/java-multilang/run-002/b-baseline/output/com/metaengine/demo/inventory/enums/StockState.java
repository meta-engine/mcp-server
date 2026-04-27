package com.metaengine.demo.inventory.enums;

/** StockState enum in the inventory domain. */
public enum StockState {
    InStock(0), Reserved(1), Depleted(2);

    private final int value;
    StockState(int value) { this.value = value; }
    public int getValue() { return value; }
}
