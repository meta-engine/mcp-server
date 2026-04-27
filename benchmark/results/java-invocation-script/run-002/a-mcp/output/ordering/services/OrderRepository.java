package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;

import java.util.List;
import java.util.Optional;

// OrderRepository service.

public class OrderRepository {

    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    public Optional<Order> findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    public List<Order> list(double limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
