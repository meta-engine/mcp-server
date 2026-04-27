package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;
import java.util.List;

/** Domain service that validates orders before mutation. */
public class OrderValidator {
    /** Validate and create an order from the provided partial input. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Validate by id. Returns null when not found. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} validated orders. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Validate a delete request for the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
