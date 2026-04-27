import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';
import { Email } from '../value-objects/Email';
import { CustomerStatus } from '../enums/CustomerStatus';

/** Customer aggregate representing a registered buyer. */
export class Customer {
  constructor(
    public readonly id: Id,
    public readonly email: Email,
    public readonly status: CustomerStatus,
    public readonly createdAt: Timestamp,
  ) {}
}
