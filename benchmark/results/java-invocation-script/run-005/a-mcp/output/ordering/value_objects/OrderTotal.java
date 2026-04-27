package com.metaengine.demo.ordering.value_objects;

// OrderTotal value object.

public class OrderTotal {
    public Integer amount;
    public String currency;

    public OrderTotal(Integer amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }
}
