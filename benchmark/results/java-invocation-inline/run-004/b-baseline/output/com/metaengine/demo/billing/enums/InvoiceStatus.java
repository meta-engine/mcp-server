package com.metaengine.demo.billing.enums;

/** InvoiceStatus enum. */
public enum InvoiceStatus {
    PENDING(0),
    PAID(1),
    OVERDUE(2),
    VOID(3);

    private final int value;

    InvoiceStatus(int value) { this.value = value; }

    public int getValue() { return value; }
}
