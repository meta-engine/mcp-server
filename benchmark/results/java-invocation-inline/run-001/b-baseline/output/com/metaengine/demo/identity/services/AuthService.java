package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** Domain service handling authentication for users. */
public class AuthService {
    /** Authenticate and create a user session from the provided partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an authenticated user by id. Returns null when not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} authenticated users. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Sign out / revoke a user by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
