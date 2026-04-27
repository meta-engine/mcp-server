package com.metaengine.demo.ordering.services;

import java.util.List;

import com.metaengine.demo.ordering.aggregates.Order;

/** OrderValidator for the ordering domain. */
public class OrderValidator {

    /** Validate and create a new Order from partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by id. Returns null if not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Orders up to the given limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the Order with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
