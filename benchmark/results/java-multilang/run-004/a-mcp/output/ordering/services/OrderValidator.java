package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;

import java.util.List;
import java.util.Optional;

// OrderValidator service.

public class OrderValidator {

    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    public Optional<Order> findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
