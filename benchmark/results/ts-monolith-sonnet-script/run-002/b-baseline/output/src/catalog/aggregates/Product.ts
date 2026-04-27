import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';
import { ProductState } from '../enums/ProductState';

/** Catalog product aggregate with pricing and lifecycle state. */
export class Product {
  constructor(
    public readonly id: Id,
    public readonly name: string,
    public readonly price: Money,
    public readonly state: ProductState,
  ) {}
}
