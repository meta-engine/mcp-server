package com.metaengine.demo.ordering.value_objects;

/** Value object representing the monetary total of an order. */
public record OrderTotal(double amount, String currency) {}
