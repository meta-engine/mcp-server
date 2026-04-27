package com.metaengine.demo.identity.services;

import com.metaengine.demo.identity.aggregates.User;
import java.util.List;

/** Domain service issuing and verifying user tokens. */
public class TokenService {
    /** Issue a token for the user described by the partial input. */
    public User create(User input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Verify a token for the given user id. Returns null when not found. */
    public User findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} active token-bearing users. */
    public List<User> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Revoke the token for the given user id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
