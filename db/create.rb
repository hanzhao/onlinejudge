#!/usr/bin/env ruby
require 'active_record'
#ActiveRecord::Base.establish_connection(adapter: 'sqlite3', database: File.expand_path('../db.sqlite', __FILE__))
# MySQL
ActiveRecord::Base.establish_connection(adapter: 'mysql2',
                                        encoding: 'utf8',
                                        reconnect: false,
                                        database: 'judge',
                                        pool: 5,
                                        username: 'judge',
                                        password: '123456',
                                        host: 'localhost')

ActiveRecord::Schema.define do

  create_table :users, force: true do |t|
    t.string   :name
    t.string   :nick
    t.string   :password
    t.integer  :admin
    t.integer  :solve
    t.integer  :submit
    t.integer  :compiler
  end

  create_table :problems, force: true do |t|
    t.string   :name
    t.integer  :timelimit
    t.integer  :memorylimit
    t.integer  :submit
    t.integer  :accept
    t.boolean  :show
    t.boolean  :judge
    t.boolean  :sj
  end

  create_table :status, force: true do |t|
    t.integer  :user_id
    t.integer  :problem_id
    t.integer  :score
    t.decimal  :time
    t.integer  :memory
    t.string   :compilemsg
    t.string   :source
    t.integer  :compiler
    t.datetime :created_time
    t.integer  :status
    t.integer  :contest_id
  end

  create_table :contests, force: true do |t|
    t.string   :name
    t.string   :problems
    t.string   :codes
    t.datetime :starttime
    t.datetime :endtime
    t.integer  :status
  end

end
