package com.metaengine.demo.inventory.value_objects;

// Quantity value object.

public class Quantity {
    public Integer amount;
    public String unit;

    public Quantity(Integer amount, String unit) {
        this.amount = amount;
        this.unit = unit;
    }
}
