package com.metaengine.demo.shipping.services;

import com.metaengine.demo.shipping.aggregates.Shipment;
import java.util.List;

/** CarrierGateway integration service in the shipping domain. */
public class CarrierGateway {
    /** Dispatch a Shipment via the carrier from a partial input. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Shipment by id, or null if not found. */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Shipments up to limit. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
