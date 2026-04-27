package com.metaengine.demo.ordering.value_objects;

// ShippingAddress value object.

public class ShippingAddress {
    public String street;
    public String city;
    public String country;
    public String postalCode;

    public ShippingAddress(String street, String city, String country, String postalCode) {
        this.street = street;
        this.city = city;
        this.country = country;
        this.postalCode = postalCode;
    }
}
