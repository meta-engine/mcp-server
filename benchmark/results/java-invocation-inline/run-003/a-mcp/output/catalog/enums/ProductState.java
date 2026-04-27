package com.metaengine.demo.catalog.enums;

// ProductState enum.

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

    public static ProductState fromValue(int value) {
        for (ProductState item : ProductState.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}
