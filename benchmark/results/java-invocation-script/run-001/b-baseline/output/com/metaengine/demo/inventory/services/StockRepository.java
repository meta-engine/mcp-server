package com.metaengine.demo.inventory.services;

import com.metaengine.demo.inventory.aggregates.StockItem;
import java.util.List;

/** StockRepository for the inventory domain. */
public class StockRepository {

    /** Persist a new StockItem. */
    public StockItem create(StockItem input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a StockItem by id; may return null. */
    public StockItem findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List stock items up to the given limit. */
    public List<StockItem> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a stock item by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
