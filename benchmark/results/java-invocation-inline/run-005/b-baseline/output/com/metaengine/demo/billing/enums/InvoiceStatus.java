package com.metaengine.demo.billing.enums;

/** Lifecycle status of an Invoice. */
public enum InvoiceStatus {
    Pending(0),
    Paid(1),
    Overdue(2),
    Void(3);

    private final int value;

    InvoiceStatus(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
