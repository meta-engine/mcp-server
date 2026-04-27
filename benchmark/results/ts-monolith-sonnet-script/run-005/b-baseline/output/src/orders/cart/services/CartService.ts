import { Id } from '../../../shared/value-objects/Id';
import { Cart } from '../aggregates/Cart';

/** Manages shopping cart operations. */
export class CartService {
  create(input: Partial<Cart>): Cart {
    void input;
    throw new Error('not implemented');
  }

  findById(id: Id): Cart | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Cart[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: Id): void {
    void id;
    throw new Error('not implemented');
  }
}
