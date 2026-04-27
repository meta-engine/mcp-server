package com.metaengine.demo.catalog.enums;

/** ProductState enum for the catalog domain. */
public enum ProductState {
    DRAFT(0),
    ACTIVE(1),
    ARCHIVED(2);

    private final int value;

    ProductState(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
