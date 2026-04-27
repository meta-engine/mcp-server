package com.metaengine.demo.catalog.value_objects;

// Price value object.

public class Price {
    public Integer amount;
    public String currency;

    public Price(Integer amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }
}
