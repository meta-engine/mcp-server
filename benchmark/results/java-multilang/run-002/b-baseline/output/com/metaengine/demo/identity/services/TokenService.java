package com.metaengine.demo.identity.services;

import java.util.List;
import com.metaengine.demo.identity.aggregates.User;

/** TokenService in the identity domain. */
public class TokenService {
    /** Create a new User. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a User by id. Returns null if not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Users up to limit. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a User by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
