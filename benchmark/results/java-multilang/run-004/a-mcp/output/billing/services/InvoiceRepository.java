package com.metaengine.demo.billing.services;

import com.metaengine.demo.billing.aggregates.Invoice;

import java.util.List;
import java.util.Optional;

// InvoiceRepository service.

public class InvoiceRepository {

    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    public Optional<Invoice> findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
