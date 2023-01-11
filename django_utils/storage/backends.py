from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage, S3ManifestStaticStorage
from storages.utils import clean_name


class BaseStorage(S3Boto3Storage):
    # This is a fix for https://github.com/jschneier/django-storages/pull/839
    # pylint: disable=arguments-differ
    def url(self, name, parameters=None, expire=None, http_method=None):
        # Preserve the trailing slash after normalizing the path.
        name = self._normalize_name(clean_name(name))
        params = parameters.copy() if parameters else {}
        if expire is None:
            expire = self.querystring_expire

        params["Bucket"] = self.bucket.name
        params["Key"] = name
        url = self.bucket.meta.client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expire,
            HttpMethod=http_method,
        )

        if self.custom_domain:
            # Key parameter can't be empty. Use "/" and remove it later.
            params["Key"] = "/"
            root_url_signed = self.bucket.meta.client.generate_presigned_url(
                "get_object", Params=params, ExpiresIn=expire
            )
            # Remove signing parameter and previouly added key "/".
            root_url = self._strip_signing_parameters(root_url_signed)[:-1]
            # Replace bucket domain with custom domain.
            custom_url = "{}//{}/".format(
                self.url_protocol, self.custom_domain
            )
            url = url.replace(root_url, custom_url)

        if self.querystring_auth:
            return url
        return self._strip_signing_parameters(url)


# We don't need to use BaseStorage here as querystring_auth is set to false
# by our upstream classes.
# pylint:disable=abstract-method
class StaticStorage(S3ManifestStaticStorage):
    location = settings.AWS_STATIC_LOCATION
    default_acl = "public-read"
    file_overwrite = True
    object_parameters = {
        "CacheControl": "max-age=86400",
    }
    gzip = True


# pylint:disable=abstract-method
class PublicMediaStorage(BaseStorage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    default_acl = "public-read"
    file_overwrite = False
    querystring_auth = False


# pylint:disable=abstract-method
class PrivateMediaStorage(BaseStorage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = "private"
    file_overwrite = False
