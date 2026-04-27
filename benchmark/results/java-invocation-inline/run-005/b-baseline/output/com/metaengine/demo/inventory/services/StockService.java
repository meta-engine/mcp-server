package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** Application service for the StockItem aggregate. */
public class StockService {

    /** Create a new StockItem from a partial input. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a StockItem by id; returns null if not found. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List StockItems, capped at the supplied limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a StockItem by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
