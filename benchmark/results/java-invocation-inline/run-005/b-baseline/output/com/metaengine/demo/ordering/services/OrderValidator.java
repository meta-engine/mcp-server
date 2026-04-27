package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;
import java.util.List;

/** Validation service for the Order aggregate. */
public class OrderValidator {

    /** Validate and create a new Order from a partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by id; returns null if not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Orders, capped at the supplied limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
