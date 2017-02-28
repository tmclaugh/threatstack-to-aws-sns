pkg_name=threatstack-to-aws-sns
pkg_description='Archive alerts from Threat Stack to AWS SNS'
pkg_version=0.1.0
pkg_origin=tmclaugh
pkg_maintainer='Tom McLaughlin'
pkg_license=('MIT')
pkg_upstream_url='https://github.com/threatstack/threatstack-to-aws-sns'
pkg_build_deps=(core/virtualenv)
pkg_deps=(core/coreutils core/python2)
pkg_exports=([http]=8080)
pkg_expose=(http)

# we copy in the source code in the `unpack` phase and need to put
# something here due to https://github.com/habitat-sh/habitat/issues/870
pkg_source="fake"

# Need to opt-out of all of these steps, as we're copying in source code
do_download() {
    return 0
}
do_verify() {
    return 0
}
do_clean() {
    return 0
}

do_unpack() {
    # Because our habitat files liver under build/.
    PROJECT_ROOT="${PLAN_CONTEXT}/.."

    mkdir -p $pkg_prefix
    build_line "Copying project data to $pkg_prefix/"
    cp -r $PROJECT_ROOT/app $pkg_prefix/
    cp -r $PROJECT_ROOT/*.py $pkg_prefix/
    cp -r $PROJECT_ROOT/requirements.txt $pkg_prefix/
}

do_build() {
    return 0
}

do_install() {
    cd $pkg_prefix
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
}


