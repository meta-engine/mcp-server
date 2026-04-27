package com.metaengine.demo.ordering.value_objects;

// BillingAddress value object.

public class BillingAddress {
    public String street;
    public String city;
    public String country;
    public String postalCode;

    public BillingAddress(String street, String city, String country, String postalCode) {
        this.street = street;
        this.city = city;
        this.country = country;
        this.postalCode = postalCode;
    }
}
