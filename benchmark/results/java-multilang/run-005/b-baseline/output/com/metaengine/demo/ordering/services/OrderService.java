package com.metaengine.demo.ordering.services;

import com.metaengine.demo.ordering.aggregates.Order;
import java.util.List;

/** OrderService service for the ordering domain. */
public class OrderService {

    /** Create a new Order. */
    public Order create(Order input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Order by id. May return null. */
    public Order findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List orders up to the given limit. */
    public List<Order> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Order by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
