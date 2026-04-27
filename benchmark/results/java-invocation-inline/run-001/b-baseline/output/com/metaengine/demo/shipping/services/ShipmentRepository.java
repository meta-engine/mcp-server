package com.metaengine.demo.shipping.services;

import com.metaengine.demo.shipping.aggregates.Shipment;
import java.util.List;

/** Persistence gateway for shipments. */
public class ShipmentRepository {
    /** Persist a new shipment from the provided partial input. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a shipment by id. Returns null when not found. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} shipments. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove a shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
