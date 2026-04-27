package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** Domain service that computes pricing for catalog products. */
public class PricingEngine {
    /** Create a priced product from the provided partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a priced product by id. Returns null when not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} priced products. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove pricing for the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
