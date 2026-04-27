package com.metaengine.demo.shipping.services;

import java.util.List;

import com.metaengine.demo.shipping.aggregates.Shipment;

/** CarrierGateway integration service. */
public class CarrierGateway {

    /** Submit a Shipment to the carrier. */
    public Shipment create(Shipment input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Shipment by id (may return null). */
    public Shipment findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List shipments up to limit. */
    public List<Shipment> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Shipment by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
