supervisorctl -c setup_env/build/go_supervisord.conf stop all
supervisorctl -c setup_env/build/go_supervisord.conf shutdown
echo "FLUSHDB" | redis-cli -n 1
# ./clear_riak.sh
rm go.db
rm setup_env/build/go_*
rm logs/*.{log,err}
./setup_env.sh
supervisord -c setup_env/build/go_supervisord.conf
./setup_env/build/go_startup_env.sh
