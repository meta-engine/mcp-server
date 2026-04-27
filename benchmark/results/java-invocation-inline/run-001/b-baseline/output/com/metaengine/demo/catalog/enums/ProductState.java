package com.metaengine.demo.catalog.enums;

/** Lifecycle states for a catalog product. */
public enum ProductState {
    Draft(0),
    Active(1),
    Archived(2);

    private final int value;

    ProductState(int value) { this.value = value; }

    public int getValue() { return value; }
}
