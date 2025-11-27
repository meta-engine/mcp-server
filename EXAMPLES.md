# MetaEngine MCP Server - Usage Examples

All examples use the new API structure with separate arrays. Examples are shown for TypeScript but work identically for Python, Go, C#, Java, Kotlin, Groovy, and Scala.

---

## Example 1: Array Types

### Input:
```json
{
  "language": "typescript",
  "initialize": true,
  "classes": [
    {"name": "Product", "typeIdentifier": "product", "properties": [{"name": "id", "primitiveType": "String"}]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "product-array", "elementTypeIdentifier": "product"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "classes": [{
    "name": "Cart",
    "typeIdentifier": "cart",
    "properties": [
      {"name": "items", "typeIdentifier": "product-array", "comment": "Products in cart"},
      {"name": "tags", "typeIdentifier": "string-array", "comment": "Cart tags"}
    ]
  }]
}
```

### Generated Output:
```typescript
// product.ts
export class Product {
  id = '';
}

// cart.ts
import { Product } from './product';

export class Cart {
  /** Products in cart */
  items = new Array<Product>();
  /** Cart tags */
  tags = new Array<string>();
}
```

---

## Example 2: Dictionary Types (All 4 Combinations)

### Input:
```json
{
  "language": "typescript",
  "initialize": true,
  "classes": [
    {"name": "User", "typeIdentifier": "user", "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Metadata", "typeIdentifier": "metadata", "properties": [{"name": "value", "primitiveType": "Any"}]}
  ],
  "dictionaryTypes": [
    {
      "typeIdentifier": "dict-prim-prim",
      "keyPrimitiveType": "String",
      "valuePrimitiveType": "Number"
    },
    {
      "typeIdentifier": "dict-prim-custom",
      "keyPrimitiveType": "String",
      "valueTypeIdentifier": "user"
    },
    {
      "typeIdentifier": "dict-custom-prim",
      "keyTypeIdentifier": "user",
      "valuePrimitiveType": "String"
    },
    {
      "typeIdentifier": "dict-custom-custom",
      "keyTypeIdentifier": "user",
      "valueTypeIdentifier": "metadata"
    }
  ],
  "classes": [{
    "name": "DataStore",
    "typeIdentifier": "store",
    "properties": [
      {"name": "scores", "typeIdentifier": "dict-prim-prim"},
      {"name": "userLookup", "typeIdentifier": "dict-prim-custom"},
      {"name": "userNames", "typeIdentifier": "dict-custom-prim"},
      {"name": "userMetadata", "typeIdentifier": "dict-custom-custom"}
    ]
  }]
}
```

### Generated Output:
```typescript
// user.ts
export class User {
  id = '';
}

// metadata.ts
export class Metadata {
  value!: unknown;
}

// data-store.ts
import { User } from './user';
import { Metadata } from './metadata';

export class DataStore {
  scores: Record<string, number> = {};
  userLookup: Record<string, User> = {};
  userNames: Record<User, string> = {};
  userMetadata: Record<User, Metadata> = {};
}
```

---

## Example 3: NestJS Service with templateRefs

### Input:
```json
{
  "language": "typescript",
  "classes": [
    {"name": "Pet", "typeIdentifier": "pet", "properties": [{"name": "name", "primitiveType": "String"}]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}
  ],
  "classes": [{
    "name": "PetService",
    "typeIdentifier": "pet-service",
    "path": "services",
    "decorators": [
      {"code": "@Injectable({ providedIn: 'root' })"}
    ],
    "customImports": [
      {"path": "@nestjs/common", "types": ["Injectable", "inject"]},
      {"path": "@nestjs/common/http", "types": ["HttpClient"]},
      {"path": "rxjs", "types": ["Observable"]}
    ],
    "customCode": [
      {"code": "private http = inject(HttpClient);"},
      {"code": "private baseUrl = '/api/pets';"},
      {
        "code": "getAll(): Observable<$petArray> { return this.http.get<$petArray>(this.baseUrl); }",
        "templateRefs": [{"placeholder": "$petArray", "typeIdentifier": "pet-array"}]
      },
      {
        "code": "getById(id: string): Observable<$pet> { return this.http.get<$pet>(`${this.baseUrl}/${id}`); }",
        "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]
      },
      {
        "code": "create(pet: $pet): Observable<$pet> { return this.http.post<$pet>(this.baseUrl, pet); }",
        "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]
      }
    ]
  }]
}
```

### Generated Output:
```typescript
// pet.ts
export class Pet {
  name!: string;
}

// services/pet-service.ts
import { Injectable, inject } from '@nestjs/common';
import { HttpClient } from '@nestjs/common/http';
import { Observable } from 'rxjs';
import { Pet } from '../pet';

@Injectable({ providedIn: 'root' })
export class PetService {

  private http = inject(HttpClient);

  private baseUrl = '/api/pets';

  getAll(): Observable<Array<Pet>> {
    return this.http.get<Array<Pet>>(this.baseUrl);
  }

  getById(id: string): Observable<Pet> {
    return this.http.get<Pet>(`${this.baseUrl}/${id}`);
  }

  create(pet: Pet): Observable<Pet> {
    return this.http.post<Pet>(this.baseUrl, pet);
  }
}
```

**Note**: Each customCode block gets automatic newlines! Template refs (`$pet`, `$petArray`) trigger automatic imports.

---

## Example 4: Generic Repository Pattern

### Input:
```json
{
  "language": "typescript",
  "classes": [
    {
      "name": "BaseEntity",
      "typeIdentifier": "base-entity",
      "isAbstract": true,
      "properties": [{"name": "id", "primitiveType": "String"}]
    },
    {
      "name": "Repository",
      "typeIdentifier": "repo-generic",
      "genericArguments": [
        {
          "name": "T",
          "constraintTypeIdentifier": "base-entity",
          "propertyName": "items",
          "isArrayProperty": true
        }
      ],
      "customCode": [
        {"code": "add(item: T): void { this.items.push(item); }"},
        {"code": "getAll(): T[] { return this.items; }"},
        {"code": "findById(id: string): T | undefined { return this.items.find(i => i.id === id); }"}
      ]
    },
    {
      "name": "User",
      "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}]
    }
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repository",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }],
  "classes": [{
    "name": "UserController",
    "typeIdentifier": "controller",
    "customCode": [{
      "code": "private repo: $userRepo = new Repository<User>();",
      "templateRefs": [{"placeholder": "$userRepo", "typeIdentifier": "user-repository"}]
    }]
  }]
}
```

### Generated Output:
```typescript
// base-entity.ts
export abstract class BaseEntity {
  id!: string;
}

// repository.ts
import { BaseEntity } from './base-entity';

export class Repository<T extends BaseEntity> {
  items!: T[];

  add(item: T): void { this.items.push(item); }

  getAll(): T[] { return this.items; }

  findById(id: string): T | undefined { return this.items.find(i => i.id === id); }
}

// user.ts
import { BaseEntity } from './base-entity';

export class User extends BaseEntity {
  email!: string;
}

// user-controller.ts
import { Repository } from './repository';
import { User } from './user';

export class UserController {

  private repo: Repository<User> = new Repository<User>();
}
```

**Note**: `concreteGenericClasses` creates the inline type `Repository<User>` with perfect imports!

---

## Example 5: Type Aliases via Custom Files

### Input:
```json
{
  "language": "typescript",
  "customFiles": [{
    "name": "types",
    "path": "utils",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Timestamp = number;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserService",
    "typeIdentifier": "service",
    "path": "services",
    "customImports": [
      {"path": "../utils/types", "types": ["UserId", "Status", "ResultSet"]}
    ],
    "customCode": [
      {"code": "async getUser(id: UserId): Promise<User> { return null as any; }"},
      {"code": "updateStatus(id: UserId, status: Status): void { }"},
      {"code": "getResults<T>(data: T[]): ResultSet<T> { return {data, total: data.length, page: 1}; }"}
    ]
  }]
}
```

### Generated Output:
```typescript
// utils/types.ts
export type UserId = string;
export type Timestamp = number;
export type Status = 'active' | 'inactive' | 'pending';
export type ResultSet<T> = { data: T[]; total: number; page: number; };

// services/user-service.ts
import { UserId, Status, ResultSet } from '../utils/types';

export class UserService {

  async getUser(id: UserId): Promise<User> {
    return null as any;
  }

  updateStatus(id: UserId, status: Status): void { }

  getResults<T>(data: T[]): ResultSet<T> {
    return {data, total: data.length, page: 1};
  }
}
```

---

## Example 6: Constructor Parameters (Critical Pattern)

### ❌ WRONG - Causes Error:
```json
{
  "language": "typescript",
  "enums": [{
    "name": "Status",
    "typeIdentifier": "status",
    "members": [{"name": "Active", "value": 1}]
  }],
  "classes": [{
    "name": "User",
    "typeIdentifier": "user",
    "constructorParameters": [
      {"name": "email", "type": "string"},
      {"name": "status", "typeIdentifier": "status"}
    ],
    "properties": [
      {"name": "email", "type": "string"},        // ❌ DUPLICATE!
      {"name": "status", "typeIdentifier": "status"},  // ❌ DUPLICATE!
      {"name": "createdAt", "primitiveType": "Date"}
    ]
  }]
}
```

**Error**: "Sequence contains more than one matching element"

### ✅ CORRECT:
```json
{
  "language": "typescript",
  "enums": [{
    "name": "Status",
    "typeIdentifier": "status",
    "members": [{"name": "Active", "value": 1}]
  }],
  "classes": [{
    "name": "User",
    "typeIdentifier": "user",
    "constructorParameters": [
      {"name": "email", "type": "string"},
      {"name": "status", "typeIdentifier": "status"}
    ],
    "properties": [
      {"name": "createdAt", "primitiveType": "Date"}  // ✅ Only ADDITIONAL properties
    ]
  }]
}
```

### Generated Output:
```typescript
import { Status } from './status.enum';

export class User {
  createdAt!: Date;

  constructor(public email: string, public status: Status) {}
}
```

**Constructor parameters automatically become properties** - don't duplicate them!

---

## Key Takeaways

1. **ArrayTypes & DictionaryTypes** - don't generate files, create reusable type references
2. **Constructor parameters** - auto-become properties, don't duplicate!
3. **One customCode per method** - automatic newlines between blocks
4. **Template refs** (`$placeholder`) - trigger automatic imports for generated types
5. **Type aliases** - use customFiles, not classes
6. **Concrete generics** - use `concreteGenericClasses` for type references like `Repository<User>`
7. **All related types** - generate in ONE call for perfect cross-references

---

For detailed explanations, see **AI_ASSISTANT_GUIDE.md**.
For quick reference, see **QUICK_START.md**.
