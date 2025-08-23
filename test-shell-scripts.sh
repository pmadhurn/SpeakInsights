#!/bin/bash
# Test script to validate shell scripts for syntax errors

echo "🧪 Testing Shell Scripts"
echo "========================"

# Test docker-deploy.sh
echo "📝 Testing docker-deploy.sh..."
if bash -n docker-deploy.sh; then
    echo "✅ docker-deploy.sh syntax is valid"
else
    echo "❌ docker-deploy.sh has syntax errors"
    exit 1
fi

# Test docker-entrypoint.sh
echo "📝 Testing docker-entrypoint.sh..."
if bash -n docker-entrypoint.sh; then
    echo "✅ docker-entrypoint.sh syntax is valid"
else
    echo "❌ docker-entrypoint.sh has syntax errors"
    exit 1
fi

# Test if scripts are executable
echo "📝 Testing file permissions..."
if [ -x docker-deploy.sh ]; then
    echo "✅ docker-deploy.sh is executable"
else
    echo "⚠️  docker-deploy.sh is not executable (run: chmod +x docker-deploy.sh)"
fi

if [ -x docker-entrypoint.sh ]; then
    echo "✅ docker-entrypoint.sh is executable"
else
    echo "⚠️  docker-entrypoint.sh is not executable (run: chmod +x docker-entrypoint.sh)"
fi

# Test help functionality
echo "📝 Testing help functionality..."
if ./docker-deploy.sh --help >/dev/null 2>&1; then
    echo "✅ docker-deploy.sh --help works"
else
    echo "❌ docker-deploy.sh --help failed"
fi

echo ""
echo "🎉 All shell script tests completed!"