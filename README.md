# Learn Vault by Flipping a Coin

Simple API Python couplé à un front qui permet de jouer au pile ou face. Au bout d'un certain score... un secret s'affiche.

- Le secret peut-être définit par l'utilisateur via la variable `SECRET_VALUE`.
- Cette application a besoin d'une base de donnée relationelle pour fonctionner correctement. Configurez la connexion avec les variables `DB_HOSTNAME`, `DB_USERNAME`, `DB_PASSWORD` et `DB_DATABASE`.
- Enfin, cette application est prévue pour devenir Vault aware. Vous pouvez donc lui passer les variables `VAULT_ADDR` et `VAULT_TOKEN`. Mais il faudra modifier le code pour que cela puisse avoir un effet quelconque.

## Forkez-moi ! Clonez-moi !

Adaptez ma CI à votre cas, pushez l'image dans votre registry (en publique).

## Utilisation de Vault avec Kubernetes

Installer [Vault](https://developer.hashicorp.com/vault/downloads) (pour la CLI).

Configurer la CLI :

```shell
vault -autocomplete-install
```

### STEP 01: Instalation du cluster

Avec l'outil de votre choix : Kind, Minikube, k3s, ...

Obtenir des informations sur le cluster Kind :

```shell
kubectl cluster-info --context kind-discovering-vault
```

### STEP 02: Installer Vault

> Helm, un chart Helm, c'est quoi ?

```shell
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm upgrade --install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \
    --namespace kube-system

helm repo add hashicorp https://helm.releases.hashicorp.com
helm upgrade --install vault hashicorp/vault \
    --namespace=vault \
    --create-namespace \
    -f manifests/vault/values.yaml
```

Créer un enregistrement DNS qui pointe sur les worker nodes (+ voir slides).

```shell
k get nodes -o wide
# /etc/hosts
# 172.18.0.2   vault.kubernetes.fr
```

> D'ailleurs, comment on crée de la haute disponibilité ?

Le cluster est en place !

> WTF ?! Le pod vault est en 0/1...

```plaintext
kubectl -n vault exec -it vault-0 -- vault operator init

    #    Unseal Key 1: HZUKc4vVbrpWpBge7ga2hekA83wEo073cssW30iaMuJp
    #    Unseal Key 2: iQy19WSM3A+Tkm27Vvv0PanHlnFNOidpPwiEteo3dZl5
    #    Unseal Key 3: dfg4+1WV4uLWfkW/4sZ2lUiJIXiwB4Qim2eeYRVvBVNV
    #    Unseal Key 4: lVo5pu0IR2Qt6MkvU8duS6QyXiWg2hdrLyfZUJNDdVa4
    #    Unseal Key 5: 72j53CfHturomZlr2KURBHSNw2baupTfPpaicovJOtdU
    #
    #    Initial Root Token: hvs.nVce65NceyR6OBn2H25pG9sn
    #
    #    Vault initialized with 5 key shares and a key threshold of 3. Please securely
    #    distribute the key shares printed above. When the Vault is re-sealed,
    #    restarted, or stopped, you must supply at least 3 of these keys to unseal it
    #    before it can start servicing requests.
    #
    #    Vault does not store the generated root key. Without at least 3 keys to
    #    reconstruct the root key, Vault will remain permanently sealed!
    #
    #    It is possible to generate new unseal keys, provided you have a quorum of
    #    existing unseal keys shares. See "vault operator rekey" for more information.
```

```shell
kubectl -n vault exec -it vault-0 -- vault operator unseal
```

```shell
export VAULT_ADDR=http://vault.kubernetes.fr:30000
vault login
```

### STEP 03: Auth Methods

- Création d'une Auth Method, on prendra la UserPass
- Création d'un utilisateur

### STEP 04: Policies

- Création d'une policy « admins »
- Affectation de la policy à notre utilisateur

### STEP 05: Installer PostgreSQL

```shell
helm upgrade --install postgresql oci://registry-1.docker.io/bitnamicharts/postgresql \
    --namespace=demo \
    --create-namespace \
    -f manifests/postgresql/values.yaml
```

Se connecter à la base de donnée pour voir si tout est ok :

```shell
sudo apt update && sudo apt install postgresql-client
kubectl port-forward --namespace demo svc/postgresql 5432:5432 &
PGPASSWORD="postgres" psql --host 127.0.0.1 -U postgres -d flip_a_coin -p 5432
```

Si vous voulez cancel le port-forward :

```shell
jobs
fg %job_id
Ctrl + C
```

### STEP 06: Installer cette superbe application

```shell
helm upgrade --install flip-a-coin manifests/flip-a-coin \
    --namespace=demo \
    --create-namespace \
    -f manifests/flip-a-coin/values.yaml
```

Si vous le souhaitez, vous pouvez créer un enregistrement DNS qui pointe sur les worker nodes, mais pour cette application cette fois (avec un nom de domaine différent).

```shell
k get nodes -o wide
# /etc/hosts
# 172.18.0.2   vault.kubernetes.fr
# 172.18.0.2   app.kubernetes.fr
```

### STEP 07: Testez l'application, affichez son secret

### STEP 08: Activer la Auth Method Kubernetes

Faites-le avec Terraform (pensez à adapter les variables !) :

```shell
cd infrastructure/vault
terraform init
terraform apply
cd -
```

Peu de configuration car Vault est déjà dans le cluster Kubernetes, et Helm nous a vachement simplifié la vie...

### STEP 09: Activer et utiliser le Secret Engine Databases

Avec les valeurs par défaut

```shell
vault secrets enable database
```

Puis, on configure ce secret engine :

```shell
vault write database/config/demo \
    plugin_name=postgresql-database-plugin \
    verify_connection=false \
    allowed_roles="*" \
    connection_url="postgresql://{{username}}:{{password}}@postgresql.demo.svc.cluster.local:5432/flip_a_coin?sslmode=disable" \
    username=postgres \
    password=postgres

vault write --force /database/rotate-root/demo
```

> T'as plus le mot de passe :-)

> NOTE: Si on veut on peut rotate à la main le mot de passe root depuis l'UI et la CLI

On crée un role readonly et un role admin :

```shell
vault write database/roles/readonly \
    db_name=demo \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    revocation_statements="ALTER ROLE \"{{name}}\" NOLOGIN;" \
    default_ttl="1h" \
    max_ttl="24h"

vault write database/roles/admin \
    db_name=demo \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT ALL ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    revocation_statements="ALTER ROLE \"{{name}}\" NOLOGIN;" \
    default_ttl="1h" \
    max_ttl="24h"
```

Bon, maintenant si tu veux un accès à la base :

```shell
vault read database/creds/readonly
# OU
vault read database/creds/admin
```

On se crée un petit role juste pour notre application :

```shell
vault write database/roles/flip_a_coin \
    db_name=demo \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
    GRANT ALL ON flip_a_coin IN SCHEMA public TO \"{{name}}\";" \
    revocation_statements="ALTER ROLE \"{{name}}\" NOLOGIN;" \
    default_ttl="1h" \
    max_ttl="24h"
```

On peut observer les utilisateurs créés sur Postgres :

```sql
\du
```

😎 DB SECURED!

Il y a toujours un secret dans les values, mais c'est un secret temporaire.

Si vraiment ça pose problème, il y a des solutions...

### STEP 10: Donner les nouvelles credentials à l'application

Côté DB on est bon.

Mais... notre application ne fonctionne plus ! Car elle n'a plus le bon secret.

Il faudrait qu'elle puisse communiquer avec Vault pour en générer un.

Ça tombe bien, nous avions activé l'Auth Method Kubernetes.

Donc n'importe quel pod de notre cluster possède une identité valide vis à vis de notre cluster Vault.  
Car ce dernier communique avec l'API Kubernetes, afin d'obtenir des informations sur les Service Account, que possèdent chaque pod de notre cluster.

> voir schema slide

Donc c'est cool, Vault sait qui est qui. On peut accorder des droits à notre application pour qu'elle puisse faire comme la commande `vault read database/creds/flip_a_coin`.

Et si possible, on voudrait accorder des droit limités... Pour cela :

```json
path "database/creds/flip_a_coin" {
  capabilities = ["read"]
}
```

Appellons cette policy « flip_a_coin_get_db_creds ».

#### Création d'un Service Account

Même si un Service Account a été automatiquement créé par Kubernetes pour notre application, il est bon d'en créer un explicitement, ne serais-ce que pour le nommage de ce dernier.

Ajoutez-le dans les templates Helm :

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Release.Name }}  # on utilise le nom de la release pour la dynamicité
automountServiceAccountToken: true
```

Ne pas oublier de le donner à notre pod : `spec.template.spec.serviceAccountName: {{ .Release.Name }}`

On upgrade :

```shell
helm upgrade --install flip-a-coin manifests/flip-a-coin \
    --namespace=demo \
    --create-namespace \
    -f manifests/flip-a-coin/values.yaml
```

#### Création du role pour la Auth Method Kubernetes

Il sert à faire le binding entre notre Service Account Kubernetes et notre policy.

```shell
vault write auth/kubernetes/role/flip_a_coin \
    bound_service_account_names=flip-a-coin \
    bound_service_account_namespaces=demo \
    policies=flip_a_coin_get_db_creds \
    ttl=1h
```

#### Rendre l'application « Vault Aware »

config.py
```python
from hvac import Client
from hvac.api.auth_methods import Kubernetes

client = Client(
    url="http://vault-internal.vault.svc.cluster.local:8200/"
)

f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')

jwt = f.read()

Kubernetes(client.adapter).login(
    role="flip_a_coin",
    jwt=jwt
)

res = client.is_authenticated()
print("res:", res)
```

Mais pas de HTTPS ici donc tant pis :'(

#### Passer les secrets via Vault CSI provider

```shell
helm upgrade --install secrets manifests/secrets \        
    --namespace=demo \
    --create-namespace \
    -f manifests/secrets/values.yaml
```

Ajouter les variables d'environment au template :

```yaml
apiVersion: apps/v1
kind: Deployment
...
spec:
  template:
    spec:
      serviceAccountName: ...
      containers:
        - name: ...
          image: ...

          env:
            - name: DB_USERNAME
              valueFrom:
                secretKeyRef:
                  name: vault-db-creds-secret
                  key: username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: vault-db-creds-secret
                  key: password

      # OU

          volumeMounts:
            - name: 'vault-db-creds'
              mountPath: '/mnt/secrets-store'
              readOnly: true
      volumes:
        - name: vault-db-creds
          csi:
            driver: 'secrets-store.csi.k8s.io'
            readOnly: true
            volumeAttributes:
              secretProviderClass: 'vault-db-creds'

```

... RIP

### For Finishers

Créer un secret kv-v2. Utiliser CSI pour le passer en variable d'enrionnement à l'application via `SECRET_VALUE`.
