# Learn Vault by Flipping a Coin

Simple API Python couplé à un front qui permet de jouer au pile ou face.Au bout d'un certain score... un secret s'affiche.

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

Ce qui donne par exemple : `172.18.0.2  vault.kubernetes.fr`

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

### STEP 03: Installer PostgreSQL

```shell
helm upgrade --install postgresql oci://registry-1.docker.io/bitnamicharts/postgresql \
    --namespace=demo \
    --create-namespace \
    -f manifests/postgresql/values.yaml
```

Se connecter à la base de donnée pour voir si tout est ok :

```shell
sudo apt update && sudo apt install postgresql-client
export POSTGRES_PASSWORD=$(kubectl get secret --namespace demo postgresql -o jsonpath="{.data.password}" | base64 -d)
kubectl port-forward --namespace demo svc/postgresql 5432:5432 &
PGPASSWORD="$POSTGRES_PASSWORD" psql --host 127.0.0.1 -U user -d flip_a_coin -p 5432
```

Si vous voulez cancel le port-forward :

```shell
jobs
fg %job_id
Ctrl + C
```

### STEP 04: Installer cette superbe application

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
