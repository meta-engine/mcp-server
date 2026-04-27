import { Id } from '../../../shared/value-objects/Id';
import { CartState } from '../enums/CartState';

/** Cart aggregate representing an active shopping cart. */
export class Cart {
  constructor(
    public readonly id: Id,
    public readonly customerId: Id,
    public readonly state: CartState,
  ) {}
}
